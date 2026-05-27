# Release Notes: v0.1.0-rc1

This is the first Lone Wolf Action Assistant Redux release candidate. Our goal for this build is simple: make Book 1 playable in the browser with a faithful Action Chart, useful automation, and enough save/replay support that players can chase routes and achievements without babysitting the bookkeeping.

## Release Status

- Supported books: **Book 1: Flight from the Dark**
- Release type: prerelease candidate
- Packaging approval: approved for final ZIP smoke testing after validation passes

## Highlights

- Book 1 character creation follows *Flight from the Dark*: Combat Skill, Endurance, five Kai Disciplines, Weaponskill, Gold Crowns, starting Weapon, Backpack, Meal, Map of Sommerlund, and monastery-find gear.
- The browser assistant now tracks Lone Wolf fields instead of the old Grey Star scaffold assumptions.
- Book 1 routes, section helpers, combat presets, random helpers, death recovery, achievements, and strategy docs are wired for local play.
- Repeat Book 1 lets a player make another run with the same core character while keeping achievement and combat history.

## Player-Facing Changes

- The Choices card is reserved for actual player choices; automation receipts now live in the status area where they are easier to skim.
- Ordinary book routes stay in the book text instead of being duplicated as extra choice buttons.
- The Book 1 map scales to fit the available screen area.
- Death and failure screens now use short themed summaries with a lighter tone.
- Hunting Meal exemptions now say clearly when Meals are unchanged.

## Automation And Rules Changes

- Required Meals, Hunting exemptions, Gold Crown gains/costs, END changes, gear gains/losses, route checks, staged rolls, and Book 1 completion are covered by audited helpers.
- Combat presets cover the checked Book 1 fights, including Mindblast immunity, forced unarmed combat, multi-enemy queues, evasion routes, timed modifiers, and victory-choice fights.
- The achievement set includes story completion, combat milestones, item discoveries, paid routes, dangerous branches, capture outcomes, gear loss, and broad exploration.

## Docs And Wiki Changes

- Public docs now describe the app in a warmer team voice and point players toward the book install guide, wiki, and first release checklist.
- The wiki mirrors the Grey Star guide structure while staying honest about Lone Wolf Book 1 support.
- The reusable Lone Wolf book pipeline documents the scan, audit, implementation, and validation workflow for later books.

## Testing

Commands:

```powershell
python -m py_compile app_server.py lonewolf_redux.py launch_lonewolf_redux.py ws_server.py
python .\testing\playtest_book1.py
```

Manual browser pass:

- User playtesting on 2026-05-27 covered at least two Book 1 browser runs with no remaining pain points reported before the release-readiness pass.

## Known Limitations

- Book 2 and later are not supported yet.
- The checked Book 1 routes are broad playable baselines, not every possible path through the book.
- Project Aon book files are not included. Players must install their own local copy of the standard HTML edition.

## Packaging Notes

- Release ZIP is created with `.\tools\Make-Release.ps1 -Version v0.1.0-rc1`.
- Confirm `git ls-files books/lw` returns no output before packaging.
- Runtime saves, UI preferences, the local wiki checkout, dist artifacts, and Project Aon book files must stay out of the package.

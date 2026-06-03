# Command Reference

The web app is the main interface. The command-line assistant still exists for keyboard-first play and debugging, but the browser UI is the normal play surface.

## Top Book Controls

- **Book 1**: open *Flight from the Dark*.
- **Current**: return to the current saved section.
- **Title**: open the current book title page.

## Status Cards

The top row shows the current book, current section, Combat Skill, Endurance, and Gold Crowns.

These cards are informational. Use the sheet controls, Vitals controls, or section helper buttons to change values.

## Section Card

- **Apply Effects**: applies audited entry effects for the current section.
- **Roll 0-9**: generates a random number like the book's random number table.
- **Route checks**: show which visible choices your current sheet supports.

Use this card for section-level play aids, especially random-number checks and current-section confirmation.

## Inventory Controls

Use **Add Item** to add:

- Weapons
- Backpack Items
- Special Items

Use **Drop Item** to remove carried items.

Use **Eat Meal** and **Missed Meal** for normal food bookkeeping. Hunting can exempt some meal checks when the book allows it.

## Tabs

- **Sheet**: character overview and new character controls.
- **Inventory**: full carried item management.
- **Disciplines**: Kai Disciplines and Discipline notes.
- **Sections**: section history and navigation support.
- **Combat**: active fight controls and combat log.
- **Saves**: save/load/import/export controls.
- **Notes**: player notes.
- **Achievements**: unlocked, locked, recent, and current-book achievement progress.

## Death Screen

When Lone Wolf dies or reaches a terminal failure, the app presents recovery options:

- **Rewind**: restore the state from before the current section visit.
- **Repeat**: try the failed section again from its ready checkpoint when that is safe.

Use Rewind when you want to undo the route choice. Use Repeat when you want to try the fight or roll again.

## Command-Line Assistant

Useful CLI commands:

- `sheet`: show the Action Chart.
- `choices`: show current section links, roll helper, combat presets, and loot options.
- `loot`: open the current section loot picker.
- `loot <number>` or `loot all`: apply audited loot.
- `drop`: remove an item by numbered slot.
- `use <item>` or `use backpack 1`: use a configured consumable.
- `combat`: show combat status.
- `combat start <name> <cs> <end>`: start tracked combat.
- `combat round [roll]`: resolve a combat round.
- `combat evade [roll]`: resolve one evasion round.
- `death`: show the active death/recovery screen.
- `repeat`: retry the failed section from its ready checkpoint when available.
- `rewind`: return to the previous section checkpoint.
- `save [path]`: save the current run.
- `load [number|path]`: load a saved run.

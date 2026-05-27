# Game Modes

Lone Wolf Action Assistant Redux has three play modes. They all use the same character, save files, achievements, and book position, so you can switch styles without starting over.

Open the Assistant menu in the upper-right of the assistant panel, then choose **Auto**, **Manual**, or **CLI**. The current mode is shown in the top bar.

## Auto Mode

Auto Mode is the recommended default.

- section effects can be applied with **Apply Effects**
- section-aware rolls and loot helpers are available
- combat presets can start tracked fights
- meals, inventory, saves, death recovery, and achievements stay active

## Manual Mode

Manual Mode keeps the sheet and bookkeeping, but turns section helper buttons into advice.

Use this when you want the book to feel closer to the paper Action Chart. You can still adjust Endurance, Combat Skill, Gold Crowns, inventory, notes, saves, and achievements. The app will not apply audited section math for you.

## CLI Mode

CLI Mode replaces the normal assistant body with the terminal assistant. It runs through the same local save data as the web app, so you can play a section in the terminal and switch back to Auto or Manual mode later.

When you enter CLI Mode, the app saves first. When you leave CLI Mode, the web assistant reloads the latest save from disk.

## What Counts As A Rule

The app treats the book text as the authority. If a section says to lose Endurance, spend Gold, lose equipment, store equipment, roll a random number, or apply a combat exception, that is the standard the assistant tries to model.

## Manual Choices

Some choices stay manual because the book gives the player discretion.

Examples:

- choosing whether to take optional loot
- choosing which item or weapon to lose when the book leaves the choice to you
- picking a route from visible book links
- deciding when to use a potion or healing item
- applying unusual one-off logic that is clearer to handle by hand

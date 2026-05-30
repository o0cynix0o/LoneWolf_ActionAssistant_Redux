# Lone Wolf Action Assistant Redux

Welcome to the project wiki for **Lone Wolf Action Assistant Redux**.

This wiki is the player-facing companion to the local web assistant. We use it to explain how the app works, what the supported books can do today, and how to keep your own Project Aon book files local and private.

The app does not include Project Aon book files. Download the books directly from Project Aon for personal use, then follow [Installing Project Aon Books](Installing-Project-Aon-Books).

## What This Project Is

Lone Wolf Action Assistant Redux is a local Python web app that acts like a digital Action Chart and play aid. It keeps the book visible on the left and the assistant on the right.

It helps with:

- Book 1 character creation
- Book 2 setup, checked routes, section helpers, combat presets, deaths, completion, and achievements
- Book 3 setup, source routes, first section helpers, first combat presets, failure/death recovery, and completion
- Book 4 and Book 5 onboarding helper builds with setup, source routes, first helpers, combat presets, completion, and repeat-book replay
- Combat Skill, Endurance, Kai Disciplines, Weapons, Backpack Items, Special Items, Meals, and Gold Crowns
- random number rolls from 0 to 9
- route checks for Kai Disciplines, items, Gold Crowns, and Endurance
- combat setup and combat round handling
- section effects, loot buttons, loss choices, and death recovery
- saves, notes, achievements, and book completion

It is designed to support the books, not replace them.

## Quick Nav

- [Getting Started](Getting-Started)
- [Installing Project Aon Books](Installing-Project-Aon-Books)
- [Command Reference](Command-Reference)
- [Game Modes](Game-Modes)
- [Combat Guide](Combat-Guide)
- [Inventory and Item Rules](Inventory-and-Item-Rules)
- [Stats and Achievements](Stats-and-Achievements)
- [Campaign and Saves](Campaign-and-Saves)
- [Public Release Guide](Public-Release-Guide)
- [Book Support Matrix](Book-Support-Matrix)
- [FAQ](FAQ)
- [Strategy Guide](Strategy-Guide)
- [Book 1 Strategy Guide](Book-1-Strategy-Guide)
- [Book 2 Strategy Guide](Book-2-Strategy-Guide)

## Current Scope

Current assistant support is strongest for:

- **Book 1: Flight from the Dark**
- **Book 2: Fire on the Water**

Book 1 is the current playable release candidate. Character creation, sheet fields, section routes, core automation, combat presets, random helpers, death recovery, achievements, and Book 1 guide pages are in place.

Book 2 now has the playable helper set in place. The app can prepare the campaign handoff or a fresh start, handle the new Kai Discipline, starting Gold, carry-over inventory, mandatory items, Royal Armoury choices, checked routes, section effects, combat presets, deaths, completion, and achievements. We still want more real-route time before calling it a public release candidate.

Book 3 has its first onboarding helper build. It can set up a fresh or continued Book 3 run, carry forward the campaign, handle the first confirmed Book 3 item/rule helpers, and complete/repeat the book. It still needs more route work and playtesting before we would talk about release-candidate status.

Books 4 and 5 have their first onboarding helper builds. Book 5 also introduces safekeeping, so selected Special Items can be stored away from the active Action Chart and carried forward later. Book 6 and later will be added one at a time through the book pipeline so new rules, carry-over choices, powers, gear, and section logic get proper attention.

## Project Rule

Book rules always win.

If the app has a convenience behavior and the book text says something else, follow the book. The assistant is meant to preserve the text's mechanics, not smooth them away into house rules.

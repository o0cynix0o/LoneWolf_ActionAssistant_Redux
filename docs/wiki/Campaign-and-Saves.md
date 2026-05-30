# Campaign and Saves

The app saves your Lone Wolf run locally.

## Autosave

Autosave is always on during normal play. Moving sections, changing inventory, resolving combat, recording death, and unlocking achievements all update the save.

That is intentional. It keeps the Action Chart and the book position together.

## Save Files

Use the **Saves** tab to:

- save now
- load a local save
- export the current save
- import a save JSON
- back up all saves

Use **Backup All Saves** before moving the app to another folder or computer.

## Death Recovery

When the run ends badly, the app preserves death history and offers recovery controls when a checkpoint is available.

- **Repeat** tries the failed section again from a ready checkpoint.
- **Rewind** restores the previous section checkpoint.

Not every death can be repeated safely. Some terminal entry effects are better handled by rewinding.

## Book Completion

Book 1 completion records a completed-book summary. Achievements can use that summary for backfill.

Book 1 can continue into the Book 2 starting setup. The assistant keeps the completed Book 1 character, adds the new Kai Discipline step, applies Book 2 starting Gold with the 50 Crown cap, preserves carry-over inventory, and handles Royal Armoury choices.

Book 2 adventure helpers are now in place, including section effects, combat presets, death recovery, completion, and achievements.

Books 3, 4, and 5 can now be played as onboarding helper builds. The assistant supports the campaign handoff, one new Kai Discipline, book-start gear choices, source routes, first section helpers, combat presets, death/failure handling, completion, and repeat-book replay. We still expect real playtesting to find rough edges before those books graduate toward release-candidate status.

Book 5 introduces safekeeping. When a book lets Lone Wolf leave selected Special Items somewhere safe, the assistant stores those items away from the active Action Chart and records where they were left. They are not available during the adventure, but they are protected from ordinary item-loss effects and can be brought forward later when the campaign calls for them.

Book 6 and later still need their own rules scan, carry-over scan, new-power step, new gear step, automation pass, and guide updates.

## Moving The App

When moving the app, keep these local folders in mind:

- `saves` stores save files.
- `data` stores app data such as last save and UI preferences.
- `books` stores your personal Project Aon book files and should not be committed or packaged.

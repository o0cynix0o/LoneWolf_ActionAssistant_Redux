# Historical Pre-Alpha Notes

These notes record the early Lone Wolf Action Assistant Redux pre-alpha rebuild. They are kept for project history; current player-facing releases start with `docs/RELEASE_NOTES_V0.1.0-rc1.md`.

## Included

- Project root renamed to match the GitHub repo.
- Grey Star Action Assistant workflow scaffold copied in as the AA2 base.
- Local Lone Wolf Book 1 source expected at `books\lw\01fftd`.
- Project Aon book files ignored by git.
- Old Lone Wolf reference data copied into `data`.
- Handoff docs created for future agents.
- Book 1 character creation rebuilt around *Flight from the Dark*:
  - Combat Skill and Endurance random digit rolls.
  - five Kai Disciplines.
  - Weaponskill random weapon.
  - Axe, one Meal, Map of Sommerlund, Gold Crowns, and monastery-find starting equipment.
- Main web sheet rebuilt around Kai Disciplines, Gold Crowns, Meals, Weapons, Backpack Items, and Special Items.
- Book 1 section-flow baseline generated from local `sect*.htm` files:
  - 350 sections.
  - 555 source route links.
  - zero invalid section links.
  - all sections reachable from section 1.
- Route buttons now use the checked-in Book 1 source-link graph and reject illegal route-button jumps.
- Book 1 simple automation baseline:
  - 47 confirmed section-effect entries.
  - required Meal handling with Hunting exemption.
  - direct END/Gold/gear/death/completion effects.
  - optional loot buttons for 18 sections.

## Historical Release Warning

At this stage, combat automation, route math, and some special item/Kai Discipline behavior were still incomplete. The project was not ready to package or publish as a playable app yet.
